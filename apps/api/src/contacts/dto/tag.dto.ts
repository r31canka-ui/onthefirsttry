import { IsOptional, IsString, Length } from 'class-validator';

export class CreateTagDto {
  @IsString()
  @Length(1, 50)
  name: string;

  @IsOptional()
  @IsString()
  color?: string;
}
