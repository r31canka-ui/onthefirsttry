import { IsEmail, IsString } from 'class-validator';

export class LoginDto {
  @IsEmail()
  email: string;

  @IsString()
  password: string;
}

export class VerifyLoginTwoFactorDto {
  @IsString()
  tempToken: string;

  @IsString()
  code: string;
}

export class MagicLinkRequestDto {
  @IsEmail()
  email: string;
}

export class MagicLinkVerifyDto {
  @IsString()
  token: string;
}

export class TwoFactorEnableDto {
  @IsString()
  code: string;
}
