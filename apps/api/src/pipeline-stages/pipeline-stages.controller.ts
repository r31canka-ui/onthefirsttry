import { Body, Controller, Delete, Get, HttpCode, HttpStatus, Param, Patch, Post } from '@nestjs/common';
import { PipelineStagesService } from './pipeline-stages.service';
import { RequirePermissions } from '../common/decorators/require-permissions.decorator';
import {
  CreatePipelineStageDto,
  ReorderPipelineStagesDto,
  UpdatePipelineStageDto,
} from './dto/pipeline-stage.dto';

@Controller('pipeline-stages')
export class PipelineStagesController {
  constructor(private readonly pipelineStagesService: PipelineStagesService) {}

  @Get()
  list() {
    return this.pipelineStagesService.list();
  }

  @RequirePermissions('pipeline.manage')
  @Post()
  create(@Body() dto: CreatePipelineStageDto) {
    return this.pipelineStagesService.create(dto);
  }

  @RequirePermissions('pipeline.manage')
  @Post('reorder')
  reorder(@Body() dto: ReorderPipelineStagesDto) {
    return this.pipelineStagesService.reorder(dto);
  }

  @RequirePermissions('pipeline.manage')
  @Patch(':id')
  update(@Param('id') id: string, @Body() dto: UpdatePipelineStageDto) {
    return this.pipelineStagesService.update(id, dto);
  }

  @RequirePermissions('pipeline.manage')
  @HttpCode(HttpStatus.NO_CONTENT)
  @Delete(':id')
  remove(@Param('id') id: string) {
    return this.pipelineStagesService.remove(id);
  }
}
