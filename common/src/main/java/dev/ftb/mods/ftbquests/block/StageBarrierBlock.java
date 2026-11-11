package dev.ftb.mods.ftbquests.block;

import dev.ftb.mods.ftbquests.FTBQuestsPlatform;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import org.jspecify.annotations.Nullable;

public class StageBarrierBlock extends QuestBarrierBlock {

	public StageBarrierBlock(Properties props) {
		super(props);
	}

	@Nullable
	@Override
	public BlockEntity newBlockEntity(BlockPos blockPos, BlockState blockState) {
		return FTBQuestsPlatform.get().stageBarrierBlockEntityProvider().create(blockPos, blockState);
	}
}
