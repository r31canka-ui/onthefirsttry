import { Body, Controller, Delete, Get, HttpCode, HttpStatus, Param, Patch, Post } from '@nestjs/common';
import { StaffService } from './staff.service';
import { RequirePermissions } from '../common/decorators/require-permissions.decorator';
import { Public } from '../common/decorators/public.decorator';
import { InviteStaffDto, UpdateStaffDto, SetStaffRoleDto, AcceptInviteDto } from './dto/staff.dto';

@Controller('staff')
export class StaffController {
  constructor(private readonly staffService: StaffService) {}

  @RequirePermissions('staff.manage')
  @Get()
  list() {
    return this.staffService.list();
  }

  @Public()
  @HttpCode(HttpStatus.OK)
  @Post('accept-invite')
  acceptInvite(@Body() dto: AcceptInviteDto) {
    return this.staffService.acceptInvite(dto);
  }

  @RequirePermissions('staff.manage')
  @Get(':id')
  findOne(@Param('id') id: string) {
    return this.staffService.findOne(id);
  }

  @RequirePermissions('staff.manage')
  @Post('invite')
  invite(@Body() dto: InviteStaffDto) {
    return this.staffService.invite(dto);
  }

  @RequirePermissions('staff.manage')
  @Patch(':id')
  update(@Param('id') id: string, @Body() dto: UpdateStaffDto) {
    return this.staffService.update(id, dto);
  }

  @RequirePermissions('staff.manage')
  @HttpCode(HttpStatus.NO_CONTENT)
  @Delete(':id')
  disable(@Param('id') id: string) {
    return this.staffService.disable(id);
  }

  @RequirePermissions('staff.manage')
  @Post(':id/roles')
  addRole(@Param('id') id: string, @Body() dto: SetStaffRoleDto) {
    return this.staffService.addRole(id, dto.roleId);
  }

  @RequirePermissions('staff.manage')
  @HttpCode(HttpStatus.NO_CONTENT)
  @Delete(':id/roles/:roleId')
  removeRole(@Param('id') id: string, @Param('roleId') roleId: string) {
    return this.staffService.removeRole(id, roleId);
  }
}
