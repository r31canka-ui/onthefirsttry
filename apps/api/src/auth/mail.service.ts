import { Injectable, Logger } from '@nestjs/common';

/**
 * Minimal mail sender for magic links / invite emails. If SMTP_* env vars
 * are configured it sends real mail via nodemailer; otherwise it logs the
 * link so Phase 1 auth is fully usable in local dev without picking an
 * email provider yet. Wiring a production transactional-email provider
 * (and templating) belongs with the rest of Phase 2 communications work -
 * flagging that choice (SendGrid/Postmark/SES/etc.) as a cost/vendor
 * decision for later, not something to lock in silently here.
 */
@Injectable()
export class MailService {
  private readonly logger = new Logger(MailService.name);

  async sendMagicLink(email: string, link: string): Promise<void> {
    if (!process.env.SMTP_HOST) {
      this.logger.warn(`[dev-mode] Magic link for ${email}: ${link}`);
      return;
    }

    const nodemailer = await import('nodemailer');
    const transport = nodemailer.createTransport({
      host: process.env.SMTP_HOST,
      port: Number(process.env.SMTP_PORT ?? 587),
      secure: process.env.SMTP_SECURE === 'true',
      auth: process.env.SMTP_USER
        ? { user: process.env.SMTP_USER, pass: process.env.SMTP_PASSWORD }
        : undefined,
    });

    await transport.sendMail({
      from: process.env.SMTP_FROM ?? 'no-reply@clinic-crm.local',
      to: email,
      subject: 'Your sign-in link',
      text: `Click to sign in: ${link}\n\nThis link expires in 15 minutes and can only be used once.`,
    });
  }

  async sendStaffInvite(email: string, link: string): Promise<void> {
    if (!process.env.SMTP_HOST) {
      this.logger.warn(`[dev-mode] Staff invite for ${email}: ${link}`);
      return;
    }

    const nodemailer = await import('nodemailer');
    const transport = nodemailer.createTransport({
      host: process.env.SMTP_HOST,
      port: Number(process.env.SMTP_PORT ?? 587),
      secure: process.env.SMTP_SECURE === 'true',
      auth: process.env.SMTP_USER
        ? { user: process.env.SMTP_USER, pass: process.env.SMTP_PASSWORD }
        : undefined,
    });

    await transport.sendMail({
      from: process.env.SMTP_FROM ?? 'no-reply@clinic-crm.local',
      to: email,
      subject: "You've been invited",
      text: `You've been invited to join your clinic's CRM. Set your password: ${link}`,
    });
  }
}
