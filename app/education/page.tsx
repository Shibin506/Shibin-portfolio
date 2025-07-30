import EducationList from '@/components/EducationList';
import { educationData } from '@/lib/educationData';

export default function EducationPage() {
  return <EducationList educationList={educationData} />;
}
