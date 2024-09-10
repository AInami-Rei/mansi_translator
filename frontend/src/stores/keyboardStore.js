import { makeAutoObservable } from "mobx";

class KeyboardStore {
  isOpen = false;

  constructor() {
    makeAutoObservable(this);
  }

  setIsOpen(value) {
    this.isOpen = value;
  }
}

export default KeyboardStore;