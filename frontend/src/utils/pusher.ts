import { useElementsStore } from "@/stores/elementsStore";
import Pusher from "pusher-js";

const elementsStore = useElementsStore()
const pusher_key = import.meta.env.MODE === 'production' ? import.meta.env.VITE_PUSHER_KEY_PROD : import.meta.env.VITE_PUSHER_KEY_DEV
const pusher_cluster = import.meta.env.VITE_PUSHER_CLUSTER
const pusher = new Pusher(pusher_key || '', {
  cluster: pusher_cluster || '',
});

pusher.connection.bind("connecting", () => {
  elementsStore.pusherState = 'connecting'
});

pusher.connection.bind("connected", () => {
  elementsStore.pusherState = 'connected'
});

pusher.connection.bind("unavailable", () => {
  elementsStore.pusherState = 'disconnected'
});

pusher.connection.bind("failed", () => {
  elementsStore.pusherState = 'failed'
});

pusher.connection.bind("disconnected", () => {
  elementsStore.pusherState = 'disconnected'
});

export default pusher;
