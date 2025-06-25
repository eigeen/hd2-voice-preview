import type { App } from "vue";

import router from "@/router";
import vuetify from "./vuetify";
import { createPinia } from "pinia";
import { PiniaColada } from "@pinia/colada";

export const installPlugins = (app: App) => {
  app.use(router).use(vuetify).use(createPinia()).use(PiniaColada, {});
};
