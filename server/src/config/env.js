import dotenv from "dotenv";
import path from "path";

dotenv.config({ path: path.resolve(process.cwd(), "../.env") });

const env = {
  BACKEND_URL: process.env.BACKEND_URL || "http://localhost:8000",
};

export default env;
