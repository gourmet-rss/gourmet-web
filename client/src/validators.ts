import { z } from "zod";

export const contentItemValidator = z.object({
  id: z.number(),
  date: z.string(),
  title: z.string(),
  description: z.string(),
  url: z.string(),
  image_url: z.string().nullable(),
  image_text: z.string().nullable(),
  content_type: z.string().nullable(),
  source_id: z.number(),
});

export const userContentItemValidator = contentItemValidator.extend({
  rating: z.number(),
  source_url: z.string(),
});

export const feedbackValidator = z.object({
  content_id: z.number(),
  rating: z.number(),
});
