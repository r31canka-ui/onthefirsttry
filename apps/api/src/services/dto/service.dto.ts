import { IsBoolean, IsInt, IsOptional, IsPositive, IsString, Length } from 'class-validator';

export class CreateServiceDto {
  @IsString()
  @Length(1, 200)
  name: string;

  @IsOptional()
  @IsString()
  category?: string;

  @IsInt()
  @IsPositive()
  durationMinutes: number;

  @IsInt()
  priceCents: number;

  @IsOptional()
  @IsString()
  @Length(3, 3)
  currency?: string;
}

export class UpdateServiceDto {
  @IsOptional()
  @IsString()
  @Length(1, 200)
  name?: string;

  @IsOptional()
  @IsString()
  category?: string;

  @IsOptional()
  @IsInt()
  @IsPositive()
  durationMinutes?: number;

  @IsOptional()
  @IsInt()
  priceCents?: number;

  @IsOptional()
  @IsString()
  @Length(3, 3)
  currency?: string;

  @IsOptional()
  @IsBoolean()
  isActive?: boolean;
}
