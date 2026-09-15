import { ArrayNotEmpty, IsArray, IsEmail, IsOptional, IsString, IsUUID, Length } from 'class-validator';

export class InviteStaffDto {
  @IsEmail()
  email: string;

  @IsString()
  @Length(2, 200)
  fullName: string;

  @IsArray()
  @ArrayNotEmpty()
  @IsUUID('4', { each: true })
  roleIds: string[];

  @IsOptional()
  @IsArray()
  @IsUUID('4', { each: true })
  locationIds?: string[];
}

export class UpdateStaffDto {
  @IsOptional()
  @IsString()
  @Length(2, 200)
  fullName?: string;

  @IsOptional()
  @IsString()
  phone?: string;

  @IsOptional()
  @IsArray()
  @IsUUID('4', { each: true })
  locationIds?: string[];
}

export class SetStaffRoleDto {
  @IsUUID('4')
  roleId: string;
}

export class AcceptInviteDto {
  @IsString()
  token: string;

  @IsString()
  @Length(12, 200)
  password: string;
}
