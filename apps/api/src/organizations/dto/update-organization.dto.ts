import { IsIn, IsOptional, IsString, Length } from 'class-validator';

export class UpdateOrganizationDto {
  @IsOptional()
  @IsString()
  @Length(2, 200)
  name?: string;

  @IsOptional()
  @IsString()
  timezone?: string;

  @IsOptional()
  @IsIn(['en', 'sq'])
  defaultLocale?: string;
}
