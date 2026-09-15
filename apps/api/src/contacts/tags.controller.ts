import { Body, Controller, Get, Post } from '@nestjs/common';
import { TagsService } from './tags.service';
import { RequirePermissions } from '../common/decorators/require-permissions.decorator';
import { CreateTagDto } from './dto/tag.dto';

@Controller('tags')
export class TagsController {
  constructor(private readonly tagsService: TagsService) {}

  @Get()
  list() {
    return this.tagsService.list();
  }

  @RequirePermissions('contacts.write')
  @Post()
  create(@Body() dto: CreateTagDto) {
    return this.tagsService.create(dto.name, dto.color);
  }
}
