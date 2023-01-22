import {
  HomeIcon,
  UserIcon,
  CogIcon,
  UserCircleIcon,
  ShieldCheckIcon,
  LockOpenIcon,
  BellSnoozeIcon,
} from "@heroicons/react/24/solid";

export const sideMenu = [
  {
    label: "Home",
    Icon: HomeIcon,
    to: "/",
  },
  {
    label: "Profile",
    Icon: UserIcon,
    to: "/profile",
  },
  {
    label: "Settings",
    Icon: CogIcon,
    to: "/settings",
    children: [
      {
        label: "Account",
        Icon: UserCircleIcon,
        to: "account",
      },
      {
        label: "Security",
        Icon: ShieldCheckIcon,
        to: "security",
        children: [
          {
            label: "Credentials",
            Icon: LockOpenIcon,
            to: "credentials",
          },
          {
            label: "2-FA",
            Icon: BellSnoozeIcon,
            to: "2fa",
          },
        ],
      },
    ],
  },
];
