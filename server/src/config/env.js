import dotenv from "dotenv";
import path from "path";

dotenv.config({ path: path.resolve(process.cwd(), "../.env") });

const env = {
  AI_SERVICE_URL: process.env.AI_SERVICE_URL || "http://localhost:8000",
};

export default env;
