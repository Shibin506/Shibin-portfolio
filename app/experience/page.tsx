import ExperienceList from '@/components/ExperienceList';
import { experienceData } from '@/lib/experienceData';

export default function ExperiencePage() {
  return <ExperienceList experienceList={experienceData} />;
}
