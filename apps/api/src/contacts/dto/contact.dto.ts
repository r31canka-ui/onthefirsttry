import { Type } from 'class-transformer';
import {
  IsBoolean,
  IsEmail,
  IsIn,
  IsInt,
  IsObject,
  IsOptional,
  IsString,
  IsUUID,
  Length,
  Max,
  Min,
} from 'class-validator';

export class CreateContactDto {
  @IsString()
  @Length(1, 200)
  firstName: string;

  @IsOptional()
  @IsString()
  lastName?: string;

  @IsOptional()
  @IsEmail()
  email?: string;

  @IsOptional()
  @IsString()
  phone?: string;

  @IsOptional()
  @IsUUID('4')
  primaryLocationId?: string;

  @IsOptional()
  @IsString()
  source?: string;

  @IsOptional()
  @IsUUID('4')
  pipelineStageId?: string;

  @IsOptional()
  @IsUUID('4')
  assignedToUserId?: string;

  @IsOptional()
  @IsObject()
  customFields?: Record<string, unknown>;

  @IsOptional()
  @IsBoolean()
  consentRecorded?: boolean;

  @IsOptional()
  @IsString()
  consentNotes?: string;
}

export class UpdateContactDto {
  @IsOptional()
  @IsString()
  @Length(1, 200)
  firstName?: string;

  @IsOptional()
  @IsString()
  lastName?: string;

  @IsOptional()
  @IsEmail()
  email?: string;

  @IsOptional()
  @IsString()
  phone?: string;

  @IsOptional()
  @IsUUID('4')
  primaryLocationId?: string;

  @IsOptional()
  @IsString()
  source?: string;

  @IsOptional()
  @IsIn(['lead', 'active_patient', 'inactive'])
  status?: string;

  @IsOptional()
  @IsUUID('4')
  assignedToUserId?: string;

  @IsOptional()
  @IsObject()
  customFields?: Record<string, unknown>;

  @IsOptional()
  @IsBoolean()
  consentRecorded?: boolean;

  @IsOptional()
  @IsString()
  consentNotes?: string;
}

export class ListContactsQueryDto {
  @IsOptional()
  @IsIn(['lead', 'active_patient', 'inactive'])
  status?: string;

  @IsOptional()
  @IsUUID('4')
  stage?: string;

  @IsOptional()
  @IsUUID('4')
  tag?: string;

  @IsOptional()
  @IsUUID('4')
  assignedTo?: string;

  @IsOptional()
  @IsUUID('4')
  locationId?: string;

  @IsOptional()
  @IsString()
  q?: string;

  @IsOptional()
  @Type(() => Number)
  @IsInt()
  @Min(1)
  page?: number = 1;

  @IsOptional()
  @Type(() => Number)
  @IsInt()
  @Min(1)
  @Max(100)
  pageSize?: number = 25;
}

export class MoveStageDto {
  @IsUUID('4')
  pipelineStageId: string;
}

export class CreateActivityDto {
  @IsString()
  @Length(1, 5000)
  body: string;

  @IsOptional()
  @IsBoolean()
  isClinical?: boolean;
}

export class AddTagDto {
  @IsUUID('4')
  tagId: string;
}
