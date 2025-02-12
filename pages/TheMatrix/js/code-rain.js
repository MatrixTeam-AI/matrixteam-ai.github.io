function initCodeRain(selector, text = 'The matrix of hackers', symbol = '', speed = 30) {
  const containers = document.querySelectorAll(selector);

  containers.forEach(container => {
    const canvas = container.querySelector('canvas') || document.createElement('canvas');
    if (!container.querySelector('canvas')) {
      container.prepend(canvas);
    }
    const ctx = canvas.getContext('2d');

    let fontSize; // 动态字体大小
    let cols; // 列数
    let down; // 每列的下落状态

    // 动态调整画布尺寸和字体大小
    function resizeCanvas() {
      const contents = container.querySelectorAll('.content');
      var contentHeight = 0;
      for(var i=0; i<contents.length; i++){
        contentHeight += contents[i].offsetHeight
      }
      canvas.width = container.clientWidth;
      canvas.height = contentHeight + 10; // 内容高度 + 微调余量，确保代码雨结束靠近底部

      fontSize = Math.max(11, canvas.width / 100); // 动态计算字体大小，最小为 14
      cols = Math.floor(canvas.width / fontSize); // 列数根据字体大小计算
      down = Array(cols).fill(0).map(() => Math.floor(Math.random() * -50)); // 初始化列状态
    }
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    function drawRain() {
      // 清除画布，模拟渐变效果
      ctx.fillStyle = 'rgba(0, 0, 0, 0.1)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // 设置字体样式
      ctx.fillStyle = '#00ff00';
      ctx.font = `${fontSize}px monospace`;

      // 绘制代码雨字符
      for (let i = 0; i < cols; i++) {
        const randomChar = text.split(symbol)[Math.floor(Math.random() * text.split(symbol).length)];
        ctx.fillText(randomChar, i * fontSize, down[i] * fontSize);

        // 如果字符超出画布，重置到顶部
        if (down[i] * fontSize > canvas.height && Math.random() > 0.9) {
          down[i] = 0;
        }
        down[i]++;
      }
    }

    setInterval(drawRain, speed);
  });
}
