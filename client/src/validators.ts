import { z } from "zod";

export const contentItemValidator = z.object({
  id: z.number(),
  title: z.string(),
  description: z.string(),
  source_id: z.number(),
})
