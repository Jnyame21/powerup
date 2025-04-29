export interface FileAttachment {
  filename:  string;
  id: number;
  url: string;
}

export interface UserData {
  id: number;
  first_name: string;
  last_name: string;
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
  created_at: string;
}
