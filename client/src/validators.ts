import { z } from "zod";

export const contentItemValidator = z.object({
  id: z.number(),
  date: z.string(),
  title: z.string(),
  description: z.string(),
  url: z.string(),
  media: z
    .array(
      z.object({
        url: z.string(),
        medium: z.string().nullable(),
        type: z.string().nullable(),
        height: z.number().nullable(),
        width: z.number().nullable(),
      }),
    )
    .nullable(),
  source_id: z.number(),
  content_type: z.string(),
});

export const userContentItemValidator = contentItemValidator.extend({
  rating: z.number(),
  source_url: z.string(),
});

export const feedbackValidator = z.object({
  content_id: z.number(),
  rating: z.number(),
});

export const flavourValidator = z.object({
  id: z.number(),
  nickname: z.string().nullable(),
});
