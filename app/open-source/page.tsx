import OpenSourceList from '@/components/OpenSourceList';
import { openSourceProject, openSourceContributions } from '@/lib/openSourceData';

export default function OpenSourcePage() {
  return (
    <OpenSourceList
      project={openSourceProject}
      contributions={openSourceContributions}
    />
  );
}
