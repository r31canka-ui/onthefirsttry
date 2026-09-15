import { createCipheriv, createDecipheriv, randomBytes } from 'node:crypto';

/**
 * AES-256-GCM at-rest encryption for sensitive columns that must not sit
 * in the DB as plaintext even though they're not queried on (2FA secrets).
 * Key comes from TWO_FACTOR_ENCRYPTION_KEY (32 raw bytes, base64-encoded).
 */
function getKey(): Buffer {
  const key = process.env.TWO_FACTOR_ENCRYPTION_KEY;
  if (!key) {
    throw new Error('TWO_FACTOR_ENCRYPTION_KEY is not set');
  }
  const buf = Buffer.from(key, 'base64');
  if (buf.length !== 32) {
    throw new Error('TWO_FACTOR_ENCRYPTION_KEY must decode to exactly 32 bytes');
  }
  return buf;
}

export function encryptSecret(plaintext: string): string {
  const iv = randomBytes(12);
  const cipher = createCipheriv('aes-256-gcm', getKey(), iv);
  const encrypted = Buffer.concat([cipher.update(plaintext, 'utf8'), cipher.final()]);
  const authTag = cipher.getAuthTag();
  return [iv.toString('base64'), authTag.toString('base64'), encrypted.toString('base64')].join('.');
}

export function decryptSecret(payload: string): string {
  const [ivB64, authTagB64, dataB64] = payload.split('.');
  const iv = Buffer.from(ivB64, 'base64');
  const authTag = Buffer.from(authTagB64, 'base64');
  const data = Buffer.from(dataB64, 'base64');
  const decipher = createDecipheriv('aes-256-gcm', getKey(), iv);
  decipher.setAuthTag(authTag);
  return Buffer.concat([decipher.update(data), decipher.final()]).toString('utf8');
}
