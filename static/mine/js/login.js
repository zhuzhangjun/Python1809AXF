$(function () {
    $('.login').width(innerWidth)
    $('#account input').blur(function () {
        var reg = /^[A-Za-z0-9]+$/
        var accountInput = $('#account input')
        if (reg.test(accountInput.val())) {
            if ($(this).val() == '') {
                return
            } else {
                $('#account i').html('')
                $('#account').removeClass('has-error').addClass('has-success')
            }

        } else {
            if ($(this).val() == '') {
                return
            } else {
                $('#account i').html('账号由数字和字母组成！')
                $('#account').removeClass('has-success').addClass('has-error')
            }
        }
    })
})