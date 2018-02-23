django.jQuery(function() {
  django.jQuery('.js').each(function() {
    var ta = document.getElementById(this.id)

    CodeMirror.fromTextArea(ta, {
      lineNumbers: true,
      styleActiveLine: true,
      matchBrackets: true,
      theme: 'solarized light'
    })
  })
})
