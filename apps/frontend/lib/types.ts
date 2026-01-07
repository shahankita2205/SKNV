export type NavLink = {
  label: string;
  href: string;
  icon: string;
};

export type NavSection = {
  section: string;
  links: NavLink[];
};

export type User = {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  navigation: NavSection[];
};
