import { createRouter, createWebHistory } from "vue-router";
import { defineAsyncComponent } from "vue";

const HomePage = defineAsyncComponent(() => import("@/views/HomePage.vue"));
const AccommodationList = defineAsyncComponent(() =>
  import("@/views/AccommodationList.vue")
);
const MapSearch = defineAsyncComponent(() => import("@/views/MapSearch.vue"));
const ProfilePage = defineAsyncComponent(() =>
  import("@/views/ProfilePage.vue")
);
const FavoritesPage = defineAsyncComponent(() =>
  import("@/views/FavoritesPage.vue")
);
const SubletPage = defineAsyncComponent(() => import("@/views/SubletPage.vue"));

const routes = [
  {
    path: "/",
    name: "home",
    component: HomePage,
    meta: { transition: "fade" },
  },
  {
    path: "/accommodation-list",
    name: "accommodation-list",
    component: AccommodationList,
    meta: { transition: "fade" },
  },
  {
    path: "/map-search",
    name: "map-search",
    component: MapSearch,
    meta: { transition: "fade" },
  },
  {
    path: "/profile",
    name: "profile",
    component: ProfilePage,
    meta: { transition: "fade" },
  },
  {
    path: "/favorites",
    name: "favorites",
    component: FavoritesPage,
    meta: { transition: "fade" },
  },
  {
    path: "/sublet",
    name: "sublet",
    component: SubletPage,
    meta: { transition: "fade" },
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

export default router;
