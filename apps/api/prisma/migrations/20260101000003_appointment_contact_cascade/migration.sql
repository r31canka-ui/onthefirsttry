-- DropForeignKey
ALTER TABLE "appointments" DROP CONSTRAINT "appointments_contact_id_fkey";

-- AddForeignKey
ALTER TABLE "appointments" ADD CONSTRAINT "appointments_contact_id_fkey" FOREIGN KEY ("contact_id") REFERENCES "contacts"("id") ON DELETE CASCADE ON UPDATE CASCADE;

