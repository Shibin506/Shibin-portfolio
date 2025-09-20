import SkillsList from '@/components/SkillsList';
import { skillsData } from '@/lib/skillsData';

export default function SkillsPage() {
  return <SkillsList skills={skillsData} />;
}
