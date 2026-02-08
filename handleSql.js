const fs = require('fs');
const readline = require('readline');

/**
 * 使用流式处理 SQL 文件，将 -- Name: 到 --Data 之间的内容替换为 DELETE FROM 表名;
 * 适用于大文件，避免内存溢出
 * @param {string} filePath - SQL 文件路径
 * @param {string} outputPath - 输出文件路径
 * @returns {Promise<void>}
 */
async function processSqlFileStream(filePath, outputPath) {
    return new Promise((resolve, reject) => {
        const inputStream = fs.createReadStream(filePath, { encoding: 'utf-8' });
        const outputStream = fs.createWriteStream(outputPath, { encoding: 'utf-8' });
        
        const rl = readline.createInterface({
            input: inputStream,
            crlfDelay: Infinity // 处理 Windows 换行符
        });
        
        let state = 'normal'; // 状态：normal, inTableDefinition
        let tableName = '';
        let buffer = []; // 用于存储需要替换的段落内容
        let lineCount = 0;
        
        rl.on('line', (line) => {
            lineCount++;
            
            // 检测 -- Name: 开头的行
            const nameMatch = line.match(/^--\s*Name:\s*([^;]+);/);
            if (nameMatch) {
                // 如果之前有未完成的段落，先输出缓冲内容
                if (state === 'inTableDefinition' && buffer.length > 0) {
                    // 输出替换内容
                    outputStream.write(`DELETE FROM ${tableName};\n\n`);
                }
                
                // 开始新的表定义段落
                state = 'inTableDefinition';
                tableName = nameMatch[1].trim();
                buffer = [line]; // 保存当前行
                return; // 不输出这一行，稍后替换
            }
            
            // 检测 --Data for 开头的行
            const dataMatch = line.match(/^--Data\s+for\s+Name:\s*[^;]+;/);
            if (dataMatch && state === 'inTableDefinition') {
                // 找到结束标记，输出替换内容
                outputStream.write(`DELETE FROM ${tableName};\n\n`);
                outputStream.write(`${line}\n`); // 输出 --Data 行
                
                // 重置状态
                state = 'normal';
                tableName = '';
                buffer = [];
                return;
            }
            
            // 如果在表定义段落中，继续缓冲
            if (state === 'inTableDefinition') {
                buffer.push(line);
            } else {
                // 正常行直接输出
                outputStream.write(`${line}\n`);
            }
        });
        
        rl.on('close', () => {
            // 处理文件末尾可能未完成的段落
            if (state === 'inTableDefinition' && buffer.length > 0) {
                outputStream.write(`DELETE FROM ${tableName};\n\n`);
            }
            
            outputStream.end();
            console.log(`处理完成！共处理 ${lineCount} 行，结果已保存到: ${outputPath}`);
            resolve();
        });
        
        rl.on('error', (error) => {
            reject(new Error(`读取文件失败: ${error.message}`));
        });
        
        outputStream.on('error', (error) => {
            reject(new Error(`写入文件失败: ${error.message}`));
        });
    });
}

/**
 * 处理 SQL 文件并输出到控制台或保存到新文件
 * @param {string} filePath - SQL 文件路径
 * @param {string} outputPath - 可选，输出文件路径，如果不提供则输出到控制台
 */
async function handleSqlFile(filePath, outputPath = null) {
    try {
        if (!outputPath) {
            // 如果没有指定输出路径，使用临时文件
            const tempPath = filePath + '.tmp';
            await processSqlFileStream(filePath, tempPath);
            
            // 读取临时文件并输出到控制台
            const content = fs.readFileSync(tempPath, 'utf-8');
            console.log(content);
            
            // 删除临时文件
            fs.unlinkSync(tempPath);
        } else {
            await processSqlFileStream(filePath, outputPath);
        }
    } catch (error) {
        console.error(`错误: ${error.message}`);
        throw error;
    }
}

// 如果直接运行此脚本，可以使用命令行参数
if (require.main === module) {
    const args = process.argv.slice(2);
    
    if (args.length === 0) {
        console.log('使用方法: node handle.js <sql文件路径> [输出文件路径]');
        console.log('示例: node handle.js input.sql output.sql');
        process.exit(1);
    }
    
    const inputPath = args[0];
    const outputPath = args[1] || null;
    
    handleSqlFile(inputPath, outputPath).catch((error) => {
        console.error(`处理失败: ${error.message}`);
        process.exit(1);
    });
}

// 导出函数供其他模块使用
module.exports = {
    processSqlFileStream,
    handleSqlFile
};
