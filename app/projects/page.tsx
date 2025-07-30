import ProjectsList from '@/components/ProjectsList';
import { projectsData } from '@/lib/projectsData';

export default function ProjectsPage() {
  return <ProjectsList projects={projectsData} />;
}
