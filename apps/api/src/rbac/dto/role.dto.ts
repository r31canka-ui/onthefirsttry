import { ArrayNotEmpty, IsArray, IsOptional, IsString, Length } from 'class-validator';
import { PermissionKey } from '../../../prisma/permissions';

export class CreateRoleDto {
  @IsString()
  @Length(2, 100)
  name: string;

  @IsArray()
  @ArrayNotEmpty()
  permissionKeys: PermissionKey[];
}

export class UpdateRoleDto {
  @IsOptional()
  @IsString()
  @Length(2, 100)
  name?: string;

  @IsOptional()
  @IsArray()
  permissionKeys?: PermissionKey[];
}
