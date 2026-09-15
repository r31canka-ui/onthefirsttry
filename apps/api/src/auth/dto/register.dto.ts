import { IsEmail, IsString, Length, Matches } from 'class-validator';

export class RegisterDto {
  @IsString()
  @Length(2, 200)
  organizationName: string;

  @IsString()
  @Length(2, 20)
  @Matches(/^[a-zA-Z]{2}$/)
  countryCode: string;

  @IsString()
  @Length(2, 200)
  fullName: string;

  @IsEmail()
  email: string;

  @IsString()
  @Length(12, 200, { message: 'Password must be at least 12 characters.' })
  password: string;
}
