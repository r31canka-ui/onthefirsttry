import { Body, Controller, Delete, Get, HttpCode, HttpStatus, Param, Patch, Post, Query } from '@nestjs/common';
import { ContactsService } from './contacts.service';
import { RequirePermissions } from '../common/decorators/require-permissions.decorator';
import {
  AddTagDto,
  CreateActivityDto,
  CreateContactDto,
  ListContactsQueryDto,
  MoveStageDto,
  UpdateContactDto,
} from './dto/contact.dto';

@Controller('contacts')
export class ContactsController {
  constructor(private readonly contactsService: ContactsService) {}

  @RequirePermissions('contacts.read')
  @Get()
  list(@Query() query: ListContactsQueryDto) {
    return this.contactsService.list(query);
  }

  @RequirePermissions('contacts.read')
  @Get(':id')
  findOne(@Param('id') id: string) {
    return this.contactsService.findOne(id);
  }

  @RequirePermissions('contacts.write')
  @Post()
  create(@Body() dto: CreateContactDto) {
    return this.contactsService.create(dto);
  }

  @RequirePermissions('contacts.write')
  @Patch(':id')
  update(@Param('id') id: string, @Body() dto: UpdateContactDto) {
    return this.contactsService.update(id, dto);
  }

  @RequirePermissions('contacts.delete')
  @HttpCode(HttpStatus.NO_CONTENT)
  @Delete(':id')
  deactivate(@Param('id') id: string) {
    return this.contactsService.deactivate(id);
  }

  @RequirePermissions('contacts.write')
  @Post(':id/stage')
  moveStage(@Param('id') id: string, @Body() dto: MoveStageDto) {
    return this.contactsService.moveStage(id, dto);
  }

  @RequirePermissions('contacts.read')
  @Get(':id/activity')
  listActivity(@Param('id') id: string) {
    return this.contactsService.listActivity(id);
  }

  @RequirePermissions('contacts.write')
  @Post(':id/activity')
  addActivity(@Param('id') id: string, @Body() dto: CreateActivityDto) {
    return this.contactsService.addActivity(id, dto);
  }

  @RequirePermissions('contacts.write')
  @Post(':id/tags')
  addTag(@Param('id') id: string, @Body() dto: AddTagDto) {
    return this.contactsService.addTag(id, dto);
  }

  @RequirePermissions('contacts.write')
  @HttpCode(HttpStatus.NO_CONTENT)
  @Delete(':id/tags/:tagId')
  removeTag(@Param('id') id: string, @Param('tagId') tagId: string) {
    return this.contactsService.removeTag(id, tagId);
  }

  @RequirePermissions('contacts.export')
  @Get(':id/export')
  exportContact(@Param('id') id: string) {
    return this.contactsService.exportContact(id);
  }

  @RequirePermissions('contacts.delete')
  @HttpCode(HttpStatus.NO_CONTENT)
  @Delete(':id/erase')
  erase(@Param('id') id: string) {
    return this.contactsService.erase(id);
  }
}
