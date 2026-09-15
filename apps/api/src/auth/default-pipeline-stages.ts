export const DEFAULT_PIPELINE_STAGES: { name: string; isWonStage?: boolean }[] = [
  { name: 'New Inquiry' },
  { name: 'Consult Booked' },
  { name: 'Consult Done' },
  { name: 'Treatment Plan Sent' },
  { name: 'Active Patient', isWonStage: true },
];
