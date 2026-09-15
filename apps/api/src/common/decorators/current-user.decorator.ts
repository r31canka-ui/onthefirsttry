import { createParamDecorator, ExecutionContext } from '@nestjs/common';
import { RequestUser } from '../../tenancy/tenant-context.interceptor';

export const CurrentUser = createParamDecorator((_: unknown, ctx: ExecutionContext): RequestUser => {
  const request = ctx.switchToHttp().getRequest();
  return request.user;
});
