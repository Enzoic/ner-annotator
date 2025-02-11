<template>
  <div>
    <classes-block />
    <div class="q-pa-lg" style="height:60vh; overflow-y:scroll;">
      <component
        :is="t.type === 'token' ? 'Token' : 'TokenBlock'"
        :id="'t' + t.start"
        v-for="t in tm.tokens"
        :token="t"
        :key="t.start"
        :backgroundColor="t.backgroundColor"
        @remove-block="onRemoveBlock"
      />
    </div>

    <div class="q-pa-md" style="border-top: 1px solid #ccc">
      <q-btn
        color="red"
        outline
        class="q-mx-md"
        @click="resetBlocks"
        label="Reset"
      />
      <q-btn
        class="q-mx-md"
        outline
        @click="backOneSentence"
        :disabled="currentIndex == 0"
        label="Back"
      />
      <q-btn
        class="q-mx-md"
        outline
        @click="skipCurrentSentence"
        label="Skip"
      />
      <q-btn
        class="q-mx-md"
        color="green"
        outline
        @click="saveTags"
        label="Save"
      />
    </div>
  </div>
</template>
<script>
import { mapState, mapMutations } from "vuex";
import Token from "./Token";
import TokenBlock from "./TokenBlock";
import ClassesBlock from "./ClassesBlock.vue";
import TokenManager from "./token-manager";
import TreebankTokenizer from "treebank-tokenizer";

export default {
  name: "AnnotationPage",
  data: function() {
    return {
      tm: new TokenManager([]),
      currentSentence: {},
      redone: "",
      tokenizer: new TreebankTokenizer(),
    };
  },
  components: {
    Token,
    TokenBlock,
    ClassesBlock,
  },
  computed: {
    ...mapState([
      "annotations",
      "classes",
      "currentClass",
      "currentIndex",
      "inputSentences",
      "enableKeyboardShortcuts",
      "filename",
    ]),
  },
  watch: {
    inputSentences() {
      this.resetIndex();
      this.tokenizeCurrentSentence();
    },
    annotations() {
      if (this.currentAnnotation != this.annotations[this.currentIndex]) {
        this.tokenizeCurrentSentence();
      }
    },
    classes() {
      this.tokenizeCurrentSentence();
    }
  },
  created() {
    if (this.inputSentences.length) {
      this.tokenizeCurrentSentence();
    }
    document.addEventListener("mouseup", this.selectTokens);
    document.addEventListener('keydown', this.keypress);
  },
  beforeUnmount() {
    document.removeEventListener("mouseup", this.selectTokens);
    document.removeEventListener("keydown", this.keypress);
  },
  methods: {
    ...mapMutations(["nextSentence", "previousSentence", "resetIndex"]),
    keypress(event) {
      if (!this.enableKeyboardShortcuts) {
        return
      }
      if (event.keyCode == 32) { // Space
        this.saveTags();
      } else if (event.keyCode == 39) { // right arrow
        this.skipCurrentSentence();
      } else if (event.keyCode == 37) { // left arrow
        this.backOneSentence();
      } else if (event.keyCode == 82 || event.keyCode == 27) { // r / R or ESC
        this.resetBlocks();
      }
      // stop event from bubbling up
      event.stopPropagation()
    },
    tokenizeCurrentSentence() {
      this.currentSentence = this.inputSentences[this.currentIndex];
      this.currentAnnotation = this.annotations[this.currentIndex];

      let tokens = this.tokenizer.tokenize(this.currentSentence.text);
      let spans = this.tokenizer.span_tokenize(this.currentSentence.text);
      let combined = tokens.map((t, i) => [spans[i][0], spans[i][1], t]);

      this.tm = new TokenManager(this.classes);
      this.tm.setTokensAndAnnotation(combined, this.currentAnnotation);
    },
    selectTokens() {
      let selection = document.getSelection();

      if (
        selection.anchorOffset === selection.focusOffset &&
        selection.anchorNode === selection.focusNode
      ) {
        return;
      }

      const rangeStart = selection.getRangeAt(0);
      const rangeEnd = selection.getRangeAt(selection.rangeCount - 1);
      let start, end, line;
      try {
        start = parseInt(rangeStart.startContainer.parentElement.id.replace("t", ""));
        let offsetEnd = parseInt(rangeEnd.endContainer.parentElement.id.replace("t", ""));
        end = offsetEnd + rangeEnd.endOffset;
        line = this.currentIndex;
      } catch {
        console.log("selected text were not tokens");
        return;
      }

      if (!this.classes.length && selection.anchorNode) {
        alert(
          "There are no Tags available. Kindly add some Tags before tagging."
        );
        selection.empty();
        return;
      }

      this.tm.addNewBlock(start, end, this.currentClass, line);
      selection.empty();
    },
    onRemoveBlock(blockStart) {
      this.tm.removeBlock(blockStart);
    },
    resetBlocks() {
      this.tm.resetBlocks();
    },
    skipCurrentSentence() {
      this.nextSentence();
      this.tokenizeCurrentSentence();
    },
    backOneSentence() {
      this.previousSentence();
      this.tokenizeCurrentSentence();
    },
    saveTags() {
      this.$store.commit("addAnnotation", {
        text: this.currentSentence.text,
        entities: this.tm.exportAsAnnotation(),
      });
      this.nextSentence();
      this.tokenizeCurrentSentence();
    },
  },
};
</script>
