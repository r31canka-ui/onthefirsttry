import { SetMetadata } from '@nestjs/common';

export const IS_PUBLIC_KEY = 'isPublic';

/** Marks a route as not requiring authentication (register/login/magic-link/health). */
export const Public = () => SetMetadata(IS_PUBLIC_KEY, true);
