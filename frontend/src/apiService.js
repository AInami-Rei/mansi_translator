import axios from "axios";

const baseUrl = '/api/';
// const baseUrl = 'http://0.0.0.0:8000/'

class ApiService {
    baseUrl = baseUrl;

    constructor() {
        this.setupHeaders()
        this.setupInstance();
    }

    setupHeaders() {
        this.headers = {
          "Content-Type": "application/json",
          accept: "application/json",
        };
      }

    setupInstance() {
        this.axiosInstance = axios.create({
          headers: this.headers,
          timeout: 10000,
          baseURL: this.baseUrl,
        });
    }

    translate = async (text, src_lang, trg_lang) => {
        return this.axiosInstance
        .post('translate', {
            "text": text, 
            "source_lang": src_lang, 
            "target_lang": trg_lang,
        })
    }
    
}

export const apiService = new ApiService();
