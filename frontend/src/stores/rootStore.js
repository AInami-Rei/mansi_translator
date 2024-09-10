import { createContext, useContext } from "react";
import KeyboardStore from "./keyboardStore";

class RootStore {
  constructor() {
    this.keyboardStore = new KeyboardStore();
  }
}

const StoreContext = createContext(new RootStore());

export const useStores = () => {
  return useContext(StoreContext);
};