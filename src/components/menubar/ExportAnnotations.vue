<template>
  <q-item clickable v-close-popup @click="generateJSONExport()">
    <q-item-section>Export</q-item-section>
  </q-item>
</template>

<script>
import { mapState } from "vuex";
import { exportFile } from "./utils";

export default {
  name: "ExportAnnotations",
  computed: {
    ...mapState(["annotations", "classes", "filename"]),
  },
  methods: {
    async generateJSONExport() {
      const output = {
        filename: this.filename,
        classes: this.classes.map((c) => c.name),
        annotations: this.annotations.map((a) => ([
          a.text,
          {entities: a.entities}
        ])),
      };
      const jsonStr = JSON.stringify(output);
      await exportFile(jsonStr, "annotations.json");
    },
  },
};
</script>
