import { PrismaClient } from '@prisma/client';
import { PERMISSIONS, SYSTEM_ROLES } from './permissions';

// Runs with the raw PrismaClient (no tenant scoping needed): it only
// touches the global permissions catalog and the org_id-IS-NULL system
// role templates, which RLS explicitly allows every tenant to read.
const prisma = new PrismaClient();

async function main() {
  for (const permission of PERMISSIONS) {
    await prisma.permission.upsert({
      where: { key: permission.key },
      update: { description: permission.description },
      create: permission,
    });
  }

  for (const [slug, role] of Object.entries(SYSTEM_ROLES)) {
    const existing = await prisma.role.findFirst({
      where: { organizationId: null, isSystemDefault: true, name: role.name },
    });

    const roleRecord =
      existing ??
      (await prisma.role.create({
        data: { name: role.name, isSystemDefault: true, organizationId: null },
      }));

    const permissionRecords = await prisma.permission.findMany({
      where: { key: { in: role.permissions } },
    });

    await prisma.rolePermission.deleteMany({ where: { roleId: roleRecord.id } });
    await prisma.rolePermission.createMany({
      data: permissionRecords.map((p) => ({ roleId: roleRecord.id, permissionId: p.id })),
      skipDuplicates: true,
    });

    console.log(`Seeded system role "${role.name}" (${slug}) with ${permissionRecords.length} permissions`);
  }
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
