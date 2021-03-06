var apiURL = 'tweets/'

Vue.component('pagination', {
  props: [
    'curPage',
    'nextPage',
    'prevPage',
    'nextPageFunction',
    'prevPageFunction'
  ],

  methods: {
    getNextPage: function() {
      this.nextPageFunction()
    },
    getPrevPage: function() {
      this.prevPageFunction()
    }
  },

  template: $('#pagination-template').html()
})

var tweets = new Vue({
  el: '#tweets',

  data: {
    page: 1,
    tweets: null
  },

  created: function() {
    this.fetchData()
  },

  watch: {
    page: 'fetchData'
  },

  filters: {
    truncate: function(v) {
      var newline = v.indexOf('\n')
      return newline > 0 ? v.slice(0, newline) : v
    },
    formatDate: function(v) {
      return v.replace(/T|Z/g, ' ')
    }
  },

  methods: {
    fetchData: function() {
      let uri = window.location.search.substring(1)
      let params = new URLSearchParams(uri)

      var xhr = new XMLHttpRequest()
      var self = this

      xhr.open('GET', apiURL + self.page + '/?' + params.toString())
      xhr.onload = function() {
        self.tweets = JSON.parse(xhr.responseText)
      }

      xhr.send()
    },
    fetchNextPage: function() {
      this.page++
    },
    fetchPrevPage: function() {
      this.page--
    }
  }
})
