import { Flow } from "@/types";
import { USE_PROCESS } from "../tryApi.constants";

export type HandleAction = (typeof USE_PROCESS)[number]["action"]["type"];
export type HandleChange =
    | React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
    | Flow["type"];
export type FormatCaps = Flow["agent_caps"];
export type TabRef = {
    handleAgent: (apiKey: string, flow: Flow) => void;
};
