import { ArrayNotEmpty, IsArray, IsBoolean, IsOptional, IsString, IsUUID, Length } from 'class-validator';

export class CreatePipelineStageDto {
  @IsString()
  @Length(1, 100)
  name: string;

  @IsOptional()
  @IsBoolean()
  isWonStage?: boolean;
}

export class UpdatePipelineStageDto {
  @IsOptional()
  @IsString()
  @Length(1, 100)
  name?: string;

  @IsOptional()
  @IsBoolean()
  isWonStage?: boolean;
}

export class ReorderPipelineStagesDto {
  @IsArray()
  @ArrayNotEmpty()
  @IsUUID('4', { each: true })
  orderedIds: string[];
}
