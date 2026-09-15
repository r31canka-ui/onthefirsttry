import { Body, Controller, Get, HttpCode, HttpStatus, Post } from '@nestjs/common';
import { AuthService } from './auth.service';
import { Public } from '../common/decorators/public.decorator';
import { CurrentUser } from '../common/decorators/current-user.decorator';
import { RequestUser } from '../tenancy/tenant-context.interceptor';
import { RegisterDto } from './dto/register.dto';
import {
  LoginDto,
  MagicLinkRequestDto,
  MagicLinkVerifyDto,
  TwoFactorEnableDto,
  VerifyLoginTwoFactorDto,
} from './dto/login.dto';

@Controller('auth')
export class AuthController {
  constructor(private readonly authService: AuthService) {}

  @Public()
  @Post('register')
  register(@Body() dto: RegisterDto) {
    return this.authService.register(dto);
  }

  @Public()
  @HttpCode(HttpStatus.OK)
  @Post('login')
  login(@Body() dto: LoginDto) {
    return this.authService.login(dto);
  }

  @Public()
  @HttpCode(HttpStatus.OK)
  @Post('login/2fa')
  verifyLoginTwoFactor(@Body() dto: VerifyLoginTwoFactorDto) {
    return this.authService.verifyLoginTwoFactor(dto.tempToken, dto.code);
  }

  @Public()
  @HttpCode(HttpStatus.OK)
  @Post('magic-link/request')
  async requestMagicLink(@Body() dto: MagicLinkRequestDto) {
    await this.authService.requestMagicLink(dto.email);
    return { message: 'If an account exists for that email, a sign-in link has been sent.' };
  }

  @Public()
  @HttpCode(HttpStatus.OK)
  @Post('magic-link/verify')
  verifyMagicLink(@Body() dto: MagicLinkVerifyDto) {
    return this.authService.verifyMagicLink(dto.token);
  }

  @HttpCode(HttpStatus.OK)
  @Post('logout')
  logout() {
    // Stateless JWTs: logout is client-side token discard. A production
    // deployment wanting server-side revocation would add a short
    // denylist (Redis, keyed by jti) here - not needed for Phase 1.
    return { message: 'Logged out.' };
  }

  @Post('2fa/setup')
  setupTwoFactor(@CurrentUser() user: RequestUser) {
    return this.authService.setupTwoFactor(user.userId, user.email);
  }

  @HttpCode(HttpStatus.OK)
  @Post('2fa/enable')
  async enableTwoFactor(@CurrentUser() user: RequestUser, @Body() dto: TwoFactorEnableDto) {
    await this.authService.enableTwoFactor(user.userId, dto.code);
    return { message: 'Two-factor authentication enabled.' };
  }

  @Get('me')
  me(@CurrentUser() user: RequestUser) {
    return user;
  }
}
