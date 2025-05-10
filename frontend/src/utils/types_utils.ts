export interface CountriesData{
  name: string
  nationality: string
}

export interface DayData {
  day: string;
  pointsEarned: number;
  duration: number;
  date: string;
  caloriesBurned: number;
  data: Workout[];
}

export interface WeekData {
  week: string;
  pointsEarned: number;
  duration: number;
  caloriesBurned: number;
  days: DayData[];
  data: Workout[];
}

export interface MonthData {
  month: string;
  pointsEarned: number;
  duration: number;
  caloriesBurned: number;
  weeks: WeekData[];
  data: Workout[];
}

export interface FileAttachment {
  filename:  string;
  id: number;
  url: string;
}

export interface UserData {
  id: number;
  email: string;
  username: string;
  last_login: string;
  img: FileAttachment | string;
  bio: string | null;
  age: number;
  gender: string;
  country: string;
  city: string;
  height: number | null;
  weight: number | null;
}

export interface WorkoutType {
  id: number;
  name: string;
  description: string;
  calories_burned_per_minute: number;
  points_per_minute: number;
  thumbnail: string;
  animation: string;
}

export interface Workout {
  id: number;
  workout_type: string;
  duration: number;
  calories_burned: number;
  points: number;
  date: string;
}

export interface UserProfile {
  id: number;
  username: string;
  email: string;
  gender: string;
  bio: string;
  country: string;
  city: string;
  age: number;
  height: number;
  weight: number;
  img: string;
}

export interface UserProfileTwo {
  id: number;
  username: string;
}

export interface ChallengeParticipant {
  id: number;
  username: string;
  points: number;
  date_joined: string;
}

export interface Challenge {
  id: number;
  name: string;
  workout_types: string[];
  description: string;
  start_date: string;
  end_date: string;
  participants: ChallengeParticipant[];
  date: string;
}

export interface Community {
  id: number;
  name: string;
  description: string;
  img: string;
  admins: UserProfileTwo[];
  members: UserProfile[];
  challenges: Challenge[];
  join_code: string;
  date: string;
}