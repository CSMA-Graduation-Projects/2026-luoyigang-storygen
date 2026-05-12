module.exports = {
    root: true,

    env: {
        node: true,
        browser: true,
        es2021: true
    },

    extends: [
        "plugin:vue/vue3-essential",
        "eslint:recommended"
    ],

    parser: "vue-eslint-parser",

    parserOptions: {
        parser: "@babel/eslint-parser",
        ecmaVersion: 2021,
        sourceType: "module",
        requireConfigFile: false
    },

    globals: {
        defineProps: "readonly",
        defineEmits: "readonly"
    },

    rules: {}
}