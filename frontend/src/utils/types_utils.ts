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
  date_of_birth: string | null
  gender: 'male' | 'female' | 'other' | null;
  location: string | null;
}

export interface WorkoutType {
  id: number;
  name: string;
  description: string;
  thumbnail: string;
  animation: string;
}

export interface Workout {
  id: number;
  workout_type: string;
  duration: number; // in minutes
  calories_burned: number;
  created_at: string;
  updated_at: string;
}
