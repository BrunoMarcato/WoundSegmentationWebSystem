<template>
  <v-app>
    <v-navigation-drawer app permanent>
      <v-list dense>
        <v-list-item-title class="text-h6 mt-4 mb-2 px-4">
          
        </v-list-item-title>

        <v-list-item link to="/inference" tag="router-link">
          <!-- <v-list-item-icon><v-icon>mdi-image-search</v-icon></v-list-item-icon> -->
          <v-icon class="mr-2">mdi-image-search</v-icon>
          <v-list-item-title>Inferência</v-list-item-title>
        </v-list-item>

        <v-list-item link to="/grouping" tag="router-link">
          <!-- <v-list-item-icon><v-icon>mdi-folder-multiple-image</v-icon></v-list-item-icon> -->
          <v-icon class="mr-2">mdi-folder-multiple-image</v-icon>
          <v-list-item-title>Agrupamento</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-navigation-drawer>

    <v-app-bar app color="primary" dark>
      <v-toolbar-title>Wound Segmenter</v-toolbar-title>
    </v-app-bar>

    <v-main>
      <v-container class="py-6">
        <router-view />
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
export default {}
</script>
