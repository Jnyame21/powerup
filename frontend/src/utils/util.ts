import { useUserAuthStore } from "@/stores/userAuthStore";

export const getWeekNumberInMonth = (date: Date): number => {
  if (!(date instanceof Date)) {
    throw new Error('Invalid date');
  }
  const day = date.getDate();
  const firstDayOfMonth = new Date(date.getFullYear(), date.getMonth(), 1).getDay()
  const weekNumber = Math.ceil((day + firstDayOfMonth) / 7);
  return weekNumber;
};

interface CountriesData{
  name: string
  nationality: string
}

export const countriesData:CountriesData[] = [
  { name: "Afghanistan", nationality: "Afghan" },
  { name: "Albania", nationality: "Albanian" },
  { name: "Algeria", nationality: "Algerian" },
  { name: "Andorra", nationality: "Andorran" },
  { name: "Angola", nationality: "Angolan" },
  { name: "Antigua and Barbuda", nationality: "Antiguan" },
  { name: "Argentina", nationality: "Argentine" },
  { name: "Armenia", nationality: "Armenian" },
  { name: "Australia", nationality: "Australian" },
  { name: "Austria", nationality: "Austrian" },
  { name: "Azerbaijan", nationality: "Azerbaijani" },
  { name: "Bahamas", nationality: "Bahamian" },
  { name: "Bahrain", nationality: "Bahraini" },
  { name: "Bangladesh", nationality: "Bangladeshi" },
  { name: "Barbados", nationality: "Barbadian" },
  { name: "Belarus", nationality: "Belarusian" },
  { name: "Belgium", nationality: "Belgian" },
  { name: "Belize", nationality: "Belizean" },
  { name: "Benin", nationality: "Beninese" },
  { name: "Bhutan", nationality: "Bhutanese" },
  { name: "Bolivia", nationality: "Bolivian" },
  { name: "Bosnia and Herzegovina", nationality: "Bosnian" },
  { name: "Botswana", nationality: "Botswanan" },
  { name: "Brazil", nationality: "Brazilian" },
  { name: "Brunei", nationality: "Bruneian" },
  { name: "Bulgaria", nationality: "Bulgarian" },
  { name: "Burkina Faso", nationality: "Burkinabe" },
  { name: "Burundi", nationality: "Burundian" },
  { name: "Cabo Verde", nationality: "Cabo Verdean" },
  { name: "Cambodia", nationality: "Cambodian" },
  { name: "Cameroon", nationality: "Cameroonian" },
  { name: "Canada", nationality: "Canadian" },
  { name: "Central African Republic", nationality: "Central African" },
  { name: "Chad", nationality: "Chadian" },
  { name: "Chile", nationality: "Chilean" },
  { name: "China", nationality: "Chinese" },
  { name: "Colombia", nationality: "Colombian" },
  { name: "Comoros", nationality: "Comorian" },
  { name: "Côte d'Ivoire", nationality: "Ivorian" },
  { name: "Croatia", nationality: "Croatian" },
  { name: "Cuba", nationality: "Cuban" },
  { name: "Cyprus", nationality: "Cypriot" },
  { name: "Czech Republic", nationality: "Czech" },
  { name: "Democratic Republic of the Congo", nationality: "Congolese" },
  { name: "Denmark", nationality: "Danish" },
  { name: "Djibouti", nationality: "Djiboutian" },
  { name: "Dominican Republic", nationality: "Dominican" },
  { name: "Ecuador", nationality: "Ecuadorian" },
  { name: "Egypt", nationality: "Egyptian" },
  { name: "El Salvador", nationality: "Salvadoran" },
  { name: "Equatorial Guinea", nationality: "Equatorial Guinean" },
  { name: "Eritrea", nationality: "Eritrean" },
  { name: "Estonia", nationality: "Estonian" },
  { name: "Eswatini", nationality: "Eswatini" },
  { name: "Ethiopia", nationality: "Ethiopian" },
  { name: "Fiji", nationality: "Fijian" },
  { name: "Finland", nationality: "Finnish" },
  { name: "France", nationality: "French" },
  { name: "Gabon", nationality: "Gabonese" },
  { name: "Gambia", nationality: "Gambian" },
  { name: "Georgia", nationality: "Georgian" },
  { name: "Germany", nationality: "German" },
  { name: "Ghana", nationality: "Ghanaian" },
  { name: "Greece", nationality: "Greek" },
  { name: "Grenada", nationality: "Grenadian" },
  { name: "Guatemala", nationality: "Guatemalan" },
  { name: "Guinea", nationality: "Guinean" },
  { name: "Guinea-Bissau", nationality: "Bissau-Guinean" },
  { name: "Guyana", nationality: "Guyanese" },
  { name: "Haiti", nationality: "Haitian" },
  { name: "Honduras", nationality: "Honduran" },
  { name: "Hungary", nationality: "Hungarian" },
  { name: "Iceland", nationality: "Icelandic" },
  { name: "India", nationality: "Indian" },
  { name: "Indonesia", nationality: "Indonesian" },
  { name: "Iran", nationality: "Iranian" },
  { name: "Iraq", nationality: "Iraqi" },
  { name: "Ireland", nationality: "Irish" },
  { name: "Israel", nationality: "Israeli" },
  { name: "Italy", nationality: "Italian" },
  { name: "Jamaica", nationality: "Jamaican" },
  { name: "Japan", nationality: "Japanese" },
  { name: "Jordan", nationality: "Jordanian" },
  { name: "Kazakhstan", nationality: "Kazakh" },
  { name: "Kenya", nationality: "Kenyan" },
  { name: "Kiribati", nationality: "Kiribati" },
  { name: "Kosovo", nationality: "Kosovar" },
  { name: "Kuwait", nationality: "Kuwaiti" },
  { name: "Kyrgyzstan", nationality: "Kyrgyz" },
  { name: "Laos", nationality: "Lao" },
  { name: "Latvia", nationality: "Latvian" },
  { name: "Lebanon", nationality: "Lebanese" },
  { name: "Lesotho", nationality: "Basotho" },
  { name: "Liberia", nationality: "Liberian" },
  { name: "Libya", nationality: "Libyan" },
  { name: "Liechtenstein", nationality: "Liechtensteiner" },
  { name: "Lithuania", nationality: "Lithuanian" },
  { name: "Luxembourg", nationality: "Luxembourger" },
  { name: "Madagascar", nationality: "Malagasy" },
  { name: "Malawi", nationality: "Malawian" },
  { name: "Malaysia", nationality: "Malaysian" },
  { name: "Maldives", nationality: "Maldivian" },
  { name: "Mali", nationality: "Malian" },
  { name: "Malta", nationality: "Maltese" },
  { name: "Marshall Islands", nationality: "Marshallese" },
  { name: "Mauritania", nationality: "Mauritanian" },
  { name: "Mauritius", nationality: "Mauritian" },
  { name: "Mexico", nationality: "Mexican" },
  { name: "Micronesia", nationality: "Micronesian" },
  { name: "Moldova", nationality: "Moldovan" },
  { name: "Monaco", nationality: "Monegasque" },
  { name: "Mongolia", nationality: "Mongolian" },
  { name: "Montenegro", nationality: "Montenegrin" },
  { name: "Morocco", nationality: "Moroccan" },
  { name: "Mozambique", nationality: "Mozambican" },
  { name: "Namibia", nationality: "Namibian" },
  { name: "Nauru", nationality: "Nauruan" },
  { name: "Nepal", nationality: "Nepali" },
  { name: "Netherlands", nationality: "Dutch" },
  { name: "New Zealand", nationality: "New Zealander" },
  { name: "Nicaragua", nationality: "Nicaraguan" },
  { name: "Niger", nationality: "Nigerien" },
  { name: "Nigeria", nationality: "Nigerian" },
  { name: "North Macedonia", nationality: "North Macedonian" },
  { name: "Norway", nationality: "Norwegian" },
  { name: "Russia", nationality: "Russian" },
  { name: "South Africa", nationality: "South African" },
  { name: "South Korea", nationality: "Korean" },
  { name: "United Kingdom", nationality: "British" },
  { name: "United States", nationality: "American" }
]

export const isStrongPassword = (password:string)=>{
  const minLength = 8;
  const hasUpperCase = /[A-Z]/.test(password);
  const hasLowerCase = /[a-z]/.test(password);
  const hasNumber = /\d/.test(password);
  const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);

  if (password.length < minLength) {
    return { strong: false, message: "Password must be at least 8 characters long" };
  }
  if (!hasUpperCase) {
    return { strong: false, message: "Password must include at least one uppercase letter" };
  }
  if (!hasLowerCase) {
    return { strong: false, message: "Password must include at least one lowercase letter" };
  }
  if (!hasNumber) {
    return { strong: false, message: "Password must include at least one number" };
  }
  if (!hasSpecialChar) {
    return { strong: false, message: "Password must include at least one special character" };
  }

  return { strong: true, message: "Password is strong!" };
}

export const  formatTime = (timeString:string)=> {
  let hours = timeString.split(":").map(Number)[0];
  const minutes = timeString.split(":").map(Number)[1]
  const ampm = hours >= 12 ? "PM" : "AM";
  hours = hours % 12 || 12; // Convert 24-hour to 12-hour format

  return `${hours}:${minutes.toString().padStart(2, "0")} ${ampm}`;
}

export const formatWorkHours = (work_hours:string)=> {
  const hours = work_hours.split(":").map(Number)[0];
  const minutes = work_hours.split(":").map(Number)[1]

  const formattedDuration = [];
  if (hours > 0) formattedDuration.push(`${hours} hr${hours > 1 ? "s" : ""}`);
  if (minutes > 0) formattedDuration.push(`${minutes} min${minutes > 1 ? "s" : ""}`);

  return formattedDuration.length > 0 ? formattedDuration.join(" ") : "0 hrs";
}

export const  formatDate = (dateString:string, format_type: string)=> {
  const date = new Date(dateString);
  let dayAbbrev = ''
  let monthAbbrev = ''
  if (format_type === 'short'){
    dayAbbrev = date.toLocaleString("en-US", { weekday: "short" }).toUpperCase();
    monthAbbrev = date.toLocaleString("en-US", { month: "short" }).toUpperCase();
  }
  else if (format_type === 'long'){
    dayAbbrev = date.toLocaleString("en-US", { weekday: "long" }).toUpperCase();
    monthAbbrev = date.toLocaleString("en-US", { month: "long" }).toUpperCase();
  }
  const day = date.getDate();

  return `${dayAbbrev}(${monthAbbrev} ${day})`;
}

export const parseFormattedDate = (formattedDate: string): string => {
  const userAuthStore = useUserAuthStore()
  // Extract the month abbreviation and day
  const match = formattedDate.match(/\((\w+)\s(\d+)\)/);
  if (!match) {
    throw new Error("Invalid date format");
  }

  const [, monthAbbrev, day] = match;

  // Convert month abbreviation to month number
  const dateObj = new Date(`${monthAbbrev} ${day}, ${new Date(userAuthStore.currentDate).getFullYear()}`);

  // Format as YYYY-MM-DD
  const year = dateObj.getFullYear();
  const month = (dateObj.getMonth() + 1).toString().padStart(2, "0"); // Ensure two digits
  const dayNum = day.padStart(2, "0"); // Ensure two digits

  return `${year}-${month}-${dayNum}`;
};

export const formatDateTime = (isoDate: string) => {
  const date = new Date(isoDate);

  const options: Intl.DateTimeFormatOptions = {
    weekday: "short",
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    hour12: true,
  };

  return date.toLocaleString("en-US", options).replace(",", "");
};


