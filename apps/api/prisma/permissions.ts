export const PERMISSIONS = [
  // Contacts
  { key: 'contacts.read', description: 'View lead/patient records' },
  { key: 'contacts.write', description: 'Create/edit lead/patient records' },
  { key: 'contacts.delete', description: 'Deactivate or erase lead/patient records' },
  { key: 'contacts.export', description: 'Export a contact record (GDPR access request)' },
  { key: 'clinical_notes.read', description: 'View clinical (is_clinical) activity entries' },
  { key: 'clinical_notes.write', description: 'Create clinical activity entries' },

  // Appointments
  { key: 'appointments.read.own', description: "View the caller's own appointments only" },
  { key: 'appointments.read.all', description: 'View all appointments at accessible locations' },
  { key: 'appointments.write', description: 'Create/reschedule/cancel appointments' },

  // Services & pipeline configuration
  { key: 'services.manage', description: 'Manage the service/treatment catalog' },
  { key: 'pipeline.manage', description: 'Manage pipeline stages' },

  // Staff & org administration
  { key: 'staff.manage', description: 'Invite/edit/disable staff and assign roles' },
  { key: 'roles.manage', description: 'Create/edit custom roles and permissions' },
  { key: 'locations.manage', description: 'Create/edit locations' },
  { key: 'organization.manage', description: "Edit the organization's own settings" },

  // Reporting
  { key: 'reports.read', description: 'View operational dashboard/reports' },
  { key: 'reports.financial.read', description: 'View financial reports (Phase 2+)' },
] as const;

export type PermissionKey = (typeof PERMISSIONS)[number]['key'];

export const SYSTEM_ROLES: Record<string, { name: string; permissions: PermissionKey[] }> = {
  owner: {
    name: 'Owner/Admin',
    permissions: PERMISSIONS.map((p) => p.key) as PermissionKey[],
  },
  provider: {
    name: 'Provider',
    permissions: [
      'contacts.read',
      'contacts.write',
      'clinical_notes.read',
      'clinical_notes.write',
      'appointments.read.own',
      'appointments.write',
      'reports.read',
    ],
  },
  front_desk: {
    name: 'Front Desk',
    permissions: [
      'contacts.read',
      'contacts.write',
      'appointments.read.all',
      'appointments.write',
      'services.manage',
    ],
  },
};
